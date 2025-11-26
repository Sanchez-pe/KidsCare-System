"""Aplicação Flask que integra com o banco Supabase do KidsCare."""
from __future__ import annotations

from typing import Dict, List

from flask import Flask, jsonify, request

from config import get_supabase_client

supabase = get_supabase_client()


def _missing_fields(payload: Dict[str, object], required: List[str]) -> List[str]:
    return [field for field in required if payload.get(field) in (None, "")]


def _execute_query(query, error_message: str):
    try:
        response = query.execute()
        return response.data, None
    except Exception as exc:  # pragma: no cover - comunicação com serviço externo
        return None, f"{error_message}: {exc}"


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/health")
    def healthcheck():
        return {"status": "ok"}

    # --------- Clientes --------- #
    @app.route("/api/clientes", methods=["GET", "POST"])
    def clientes():
        if request.method == "GET":
            status = request.args.get("status")
            query = supabase.table("clientes").select("*")
            if status:
                query = query.eq("status", status)

            data, error = _execute_query(query, "Erro ao listar clientes")
            if error:
                return jsonify({"error": error}), 500
            return jsonify(data)

        payload = request.get_json(force=True, silent=True) or {}
        required = ["nome", "data_nascimento", "cpf", "email", "status"]
        missing = _missing_fields(payload, required)
        if missing:
            return jsonify({"error": f"Campos obrigatórios ausentes: {', '.join(missing)}"}), 400

        data, error = _execute_query(
            supabase.table("clientes").insert(payload), "Erro ao criar cliente"
        )
        if error:
            return jsonify({"error": error}), 500

        return jsonify(data[0]), 201

    @app.route("/api/clientes/<int:cliente_id>", methods=["GET", "PUT"])
    def cliente_detail(cliente_id: int):
        if request.method == "GET":
            data, error = _execute_query(
                supabase.table("clientes").select("*").eq("id", cliente_id),
                "Erro ao buscar cliente",
            )
            if error:
                return jsonify({"error": error}), 500
            if not data:
                return jsonify({"error": "Cliente não encontrado"}), 404
            return jsonify(data[0])

        payload = request.get_json(force=True, silent=True) or {}
        data, error = _execute_query(
            supabase.table("clientes").update(payload).eq("id", cliente_id),
            "Erro ao atualizar cliente",
        )
        if error:
            return jsonify({"error": error}), 500
        if not data:
            return jsonify({"error": "Cliente não encontrado"}), 404
        return jsonify(data[0])

    # --------- Médicos --------- #
    @app.route("/api/medicos", methods=["GET", "POST"])
    def medicos():
        if request.method == "GET":
            disponivel = request.args.get("disponivel")
            especialidade = request.args.get("especialidade")

            query = supabase.table("medicos").select("*")
            if disponivel is not None:
                query = query.eq("disponivel", disponivel.lower() in ["1", "true", "sim"])
            if especialidade:
                query = query.ilike("especialidade", f"%{especialidade}%")

            data, error = _execute_query(query, "Erro ao listar médicos")
            if error:
                return jsonify({"error": error}), 500
            return jsonify(data)

        payload = request.get_json(force=True, silent=True) or {}
        required = ["nome", "crm", "especialidade", "email", "status"]
        missing = _missing_fields(payload, required)
        if missing:
            return jsonify({"error": f"Campos obrigatórios ausentes: {', '.join(missing)}"}), 400

        data, error = _execute_query(
            supabase.table("medicos").insert(payload), "Erro ao criar médico"
        )
        if error:
            return jsonify({"error": error}), 500

        return jsonify(data[0]), 201

    @app.route("/api/medicos/<int:medico_id>", methods=["GET", "PUT"])
    def medico_detail(medico_id: int):
        if request.method == "GET":
            data, error = _execute_query(
                supabase.table("medicos").select("*").eq("id", medico_id),
                "Erro ao buscar médico",
            )
            if error:
                return jsonify({"error": error}), 500
            if not data:
                return jsonify({"error": "Médico não encontrado"}), 404
            return jsonify(data[0])

        payload = request.get_json(force=True, silent=True) or {}
        data, error = _execute_query(
            supabase.table("medicos").update(payload).eq("id", medico_id),
            "Erro ao atualizar médico",
        )
        if error:
            return jsonify({"error": error}), 500
        if not data:
            return jsonify({"error": "Médico não encontrado"}), 404
        return jsonify(data[0])

    # --------- Datas de atendimento --------- #
    @app.route("/api/datas-atendimento", methods=["GET", "POST"])
    def datas_atendimento():
        if request.method == "GET":
            medico_id = request.args.get("medico_id")
            disponivel = request.args.get("disponivel")

            query = supabase.table("datas_atendimento").select("*")
            if medico_id:
                query = query.eq("medico_id", int(medico_id))
            if disponivel is not None:
                query = query.eq("disponivel", disponivel.lower() in ["1", "true", "sim"])

            data, error = _execute_query(query, "Erro ao listar datas de atendimento")
            if error:
                return jsonify({"error": error}), 500
            return jsonify(data)

        payload = request.get_json(force=True, silent=True) or {}
        required = ["medico_id", "data", "hora_inicio", "hora_fim", "disponivel", "status"]
        missing = _missing_fields(payload, required)
        if missing:
            return jsonify({"error": f"Campos obrigatórios ausentes: {', '.join(missing)}"}), 400

        data, error = _execute_query(
            supabase.table("datas_atendimento").insert(payload),
            "Erro ao criar data de atendimento",
        )
        if error:
            return jsonify({"error": error}), 500

        return jsonify(data[0]), 201

    # --------- Atendimentos --------- #
    @app.route("/api/atendimentos", methods=["GET", "POST"])
    def atendimentos():
        if request.method == "GET":
            cliente_id = request.args.get("cliente_id")
            medico_id = request.args.get("medico_id")
            status = request.args.get("status")

            query = supabase.table("atendimentos").select("*")
            if cliente_id:
                query = query.eq("clientes_id", int(cliente_id))
            if medico_id:
                query = query.eq("medicos_id", int(medico_id))
            if status:
                query = query.eq("status", status)

            data, error = _execute_query(query, "Erro ao listar atendimentos")
            if error:
                return jsonify({"error": error}), 500
            return jsonify(data)

        payload = request.get_json(force=True, silent=True) or {}
        required = [
            "clientes_id",
            "medicos_id",
            "data_atendimento_id",
            "horario",
            "tipo_atendimento",
            "status",
        ]
        missing = _missing_fields(payload, required)
        if missing:
            return jsonify({"error": f"Campos obrigatórios ausentes: {', '.join(missing)}"}), 400

        data, error = _execute_query(
            supabase.table("atendimentos").insert(payload),
            "Erro ao criar atendimento",
        )
        if error:
            return jsonify({"error": error}), 500

        return jsonify(data[0]), 201

    @app.route("/api/atendimentos/<int:atendimento_id>", methods=["GET", "PUT"])
    def atendimento_detail(atendimento_id: int):
        if request.method == "GET":
            data, error = _execute_query(
                supabase.table("atendimentos").select("*").eq("id", atendimento_id),
                "Erro ao buscar atendimento",
            )
            if error:
                return jsonify({"error": error}), 500
            if not data:
                return jsonify({"error": "Atendimento não encontrado"}), 404
            return jsonify(data[0])

        payload = request.get_json(force=True, silent=True) or {}
        data, error = _execute_query(
            supabase.table("atendimentos").update(payload).eq("id", atendimento_id),
            "Erro ao atualizar atendimento",
        )
        if error:
            return jsonify({"error": error}), 500
        if not data:
            return jsonify({"error": "Atendimento não encontrado"}), 404
        return jsonify(data[0])

    # --------- Pagamentos --------- #
    @app.route("/api/pagamentos", methods=["GET", "POST"])
    def pagamentos():
        if request.method == "GET":
            atendimento_id = request.args.get("atendimento_id")
            status = request.args.get("status")

            query = supabase.table("pagamentos").select("*")
            if atendimento_id:
                query = query.eq("atendimento_id", int(atendimento_id))
            if status:
                query = query.eq("status", status)

            data, error = _execute_query(query, "Erro ao listar pagamentos")
            if error:
                return jsonify({"error": error}), 500
            return jsonify(data)

        payload = request.get_json(force=True, silent=True) or {}
        required = ["atendimento_id", "valor", "metodo_pagamento", "status"]
        missing = _missing_fields(payload, required)
        if missing:
            return jsonify({"error": f"Campos obrigatórios ausentes: {', '.join(missing)}"}), 400

        data, error = _execute_query(
            supabase.table("pagamentos").insert(payload), "Erro ao registrar pagamento"
        )
        if error:
            return jsonify({"error": error}), 500

        return jsonify(data[0]), 201

    @app.route("/api/pagamentos/<int:pagamento_id>", methods=["PUT"])
    def pagamento_detail(pagamento_id: int):
        payload = request.get_json(force=True, silent=True) or {}
        data, error = _execute_query(
            supabase.table("pagamentos").update(payload).eq("id", pagamento_id),
            "Erro ao atualizar pagamento",
        )
        if error:
            return jsonify({"error": error}), 500
        if not data:
            return jsonify({"error": "Pagamento não encontrado"}), 404
        return jsonify(data[0])

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000, debug=True)

